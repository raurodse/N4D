#!/usr/bin/perl -w
use File::Basename;
use JSON; # depend libjson-perl on ubuntu
use File::Temp qw/ tempfile tempdir /;
use lib( "/usr/share/n4d/perl-plugins" );
my @files = </usr/share/n4d/perl-plugins/*.pm>;
foreach $file( @files ){
        
        ( my $module = basename( $file ) ) =~ s/\.[^.]+$//;
        eval "use $module";
}
my ( $class, $function, $pipe ) = @ARGV;
if( -e "$pipe")
{
	`echo $pipe > /tmp/milog`;
        open( my $fh, '<', "$pipe" );
        $json_text   = <$fh>;
        $perl_scalar = decode_json( $json_text );
        
        my $aux = new $class();
        my ($fileh,$filename) = tempfile();
        print $fileh encode_json( { result => $aux->$function( @{ $perl_scalar->{ 'args' } } ) } );
	unlink($pipe);
        print $filename;
	exit 0
}
exit 1;
